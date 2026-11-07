#!/usr/bin/env bash
# Local, incremental LineageOS 23.2 / Android 16 build for the prepared workspace.
set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
root=$PWD
jobs=4
check_only=false
clean=false
gapps=none

usage() {
 cat <<'EOF'
Сборка LineageOS 23.2 / Android 16 (user, ARM64 GSI).

  ./build.sh --gapps none       vanilla без Google (по умолчанию)
  ./build.sh --gapps minimal    минимальные Google-сервисы + Play Store
  ./build.sh --gapps full       расширенный комплект MindTheGapps (см. docs/BUILD_VARIANTS.md)
  ./build.sh --jobs 4           число параллельных задач (по умолчанию 4)
  ./build.sh --clean            очистить кэш только выбранного варианта
  ./build.sh --check            проверить подготовку без компиляции/скачивания
  ./build.sh --help             показать справку

Варианты имеют раздельные рабочие каталоги и продолжают свою сборку.
Готовые образы: out/<вариант>/<дата-SHA256>/system.img; ссылка latest — последний.
--clean не удаляет архивы готовых образов. Ctrl+C останавливает сборку.
Недостающие GApps скачиваются с закреплённой ревизии при обычном запуске.
EOF
}

while (($#)); do
 case "$1" in
  --gapps)
   [[ $# -ge 2 && $2 =~ ^(none|minimal|full)$ ]] || {
    echo "После --gapps укажите none, minimal или full." >&2; exit 2;
   }
   gapps=$2; shift 2 ;;
  --jobs)
   [[ $# -ge 2 && $2 =~ ^[1-9][0-9]*$ ]] || {
    echo 'Ошибка: после --jobs нужно положительное целое число.' >&2; exit 2;
   }
   jobs=$2; shift 2 ;;
  --check) check_only=true; shift ;;
  --clean) clean=true; shift ;;
  --help|-h) usage; exit 0 ;;
  *) echo "Неизвестный аргумент: $1" >&2; usage >&2; exit 2 ;;
 esac
done

if $clean && $check_only; then
 echo '--clean и --check нельзя использовать вместе.' >&2; exit 2
fi

source "$root/scripts/env.sh"
for tool in git python3 flock tee rsync make bison flex zip unzip gperf bc; do
 command -v "$tool" >/dev/null || { echo "Не найден инструмент: $tool" >&2; exit 1; }
done
if ! $check_only; then
 command -v systemd-run >/dev/null || {
  echo 'Для сборки нужен systemd-run: запуск без лимита памяти запрещён.' >&2; exit 1;
 }
fi
[[ -d source/.repo && -f source/build/envsetup.sh && -s research/resolved-manifest.xml ]] || {
 echo "Исходники не подготовлены. См. $root/docs/BUILD.md" >&2; exit 1;
}
python3 - <<'PY'
from pathlib import Path
from zipfile import is_zipfile
for arch in ('arm', 'arm64'):
    apk = Path('source/external/chromium-webview/prebuilt') / arch / 'webview.apk'
    if not apk.is_file() or not is_zipfile(apk):
        raise SystemExit(f'Нет полноценного WebView APK: {apk}. См. раздел Git LFS в docs/BUILD.md.')
PY

case "$gapps" in
 none) variant=vanilla; build_out="$root/source/out" ;;
 minimal|full) variant="gapps-$gapps"; build_out="$root/source/out-$variant" ;;
esac
# Explicit paths prevent an inherited OUT_DIR from mixing variants.
export OUT_DIR="${build_out##*/}"
unset OUT_DIR_COMMON_BASE
image="$build_out/target/product/tdgsi_arm64_ab/system.img"
echo "Цель: LineageOS 23.2 / Android 16, $variant ARM64 A/B EXT4 GSI"
echo "Рабочие файлы: $build_out"
echo "Образы: $root/out/$variant/"
echo "Рабочая папка: $root"
echo "Параллельных задач: $jobs"
if $check_only; then
 python3 "$root/scripts/prepare-gapps.py" --variant "$gapps" --check
 echo 'Предварительная проверка пройдена. Компиляция не запускалась.'
 exit 0
fi

# Keep the lock through artifact inspection as well as compilation.
exec 9>"$root/cache/build.lock"
flock -n 9 || { echo 'Сборка уже запущена другим экземпляром build.sh.' >&2; exit 1; }
mkdir -p logs
log=$(mktemp "$root/logs/build-$variant-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX.log")
ln -sfn "${log##*/}" "$root/logs/latest-build.log"
echo "Лог: $log"
echo 'Для остановки нажмите Ctrl+C и дождитесь возврата приглашения терминала.'
# Preserve even a successful image left behind before inspection/publication.
if [[ -s "$image" ]]; then
 python3 "$root/scripts/archive-image.py" --variant "$variant" --image "$image" --preserve-only
fi
if $clean; then
 [[ $(realpath -m "$build_out") == "$build_out" && ! -L "$build_out" ]] || {
  echo 'Отказ от очистки: рабочий каталог указывает за пределы ожидаемого каталога.' >&2; exit 1;
 }
 echo "Чистая сборка: удаляю $build_out" | tee -a "$log"
 rm -rf -- "$build_out"
fi
interrupted=false
unit="lapis-build-$$"
trap 'interrupted=true; systemctl --user stop "$unit.scope" >/dev/null 2>&1 || true' INT TERM

set +e
systemd-run --user --scope --unit="$unit" --quiet \
 -p MemoryHigh=44G -p MemoryMax=48G -p MemorySwapMax=0 -p OOMPolicy=kill \
 /usr/bin/env "LAPIS_GAPPS=$gapps" "BUILD_JOBS=$jobs" GOGC=30 GOMEMLIMIT=30GiB \
 /usr/bin/bash "$root/scripts/build-baseline.sh" 2>&1 | tee "$log"
results=("${PIPESTATUS[@]}")
set -e
if $interrupted || [[ ${results[0]} == 130 || ${results[0]} == 143 ]]; then
 echo "Сборка остановлена. Результаты сохранены; повторите запуск для продолжения. Лог: $log"
 exit 130
fi
if [[ ${results[0]} != 0 ]]; then
 echo "Сборка завершилась с ошибкой (код ${results[0]}). Лог: $log" >&2
 echo 'Исправьте причину и повторите запуск. Очистка out для продолжения не нужна.' >&2
 exit "${results[0]}"
fi
if [[ ${results[1]} != 0 ]]; then
 echo "Не удалось полностью записать лог: $log" >&2
 exit 1
fi

[[ -s "$image" ]] || { echo "Сборка вернула успех, но образ отсутствует: $image" >&2; exit 1; }
set +e
python3 "$root/scripts/inspect-image.py" "$image" --output "$root/artifacts/$variant-system.img.inspection.json" 2>&1 | tee -a "$log"
inspection_status=$?
set -e
if [[ $inspection_status != 0 ]]; then
 echo "Образ создан, но запись его проверочных данных не завершилась. Лог: $log" >&2
 exit "$inspection_status"
fi
python3 "$root/scripts/archive-image.py" --variant "$variant" --image "$image" \
 --inspection "$root/artifacts/$variant-system.img.inspection.json" --log "$log"
echo "Образ собран: $root/out/$variant/latest/system.img"
echo "SHA256 и сведения находятся рядом с образом."
echo 'Это экспериментальная сборка: работа нового образа на телефоне ещё не проверена.'

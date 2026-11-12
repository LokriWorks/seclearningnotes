#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p records
record_dir=$(mktemp -d "$PWD/records/run-XXXXXXXX")
exec > >(tee "$record_dir/operations.log") 2>&1
trap 'status=$?; printf "\n实验脚本退出状态：%s\n" "$status"' EXIT
PS4='+ ${LINENO}: '
step() { printf '\n【%s】\n' "$1"; }
step '一、检查环境：保留现有文件；记录使用北京时间和工具版本'
set -x
TZ=Asia/Shanghai date --iso-8601=seconds
pwd
ls -la
uname -srmo
gcc --version
make --version
command -v more less tar gzip bzip2
set +x
step '二、目录与文件：在本次独立目录创建练习文件，复制、移动并删除本次副本'
set -x
mkdir "$record_dir/shell"
cd "$record_dir/shell"
pwd
mkdir empty
touch notes.txt
printf 'Linux Shell\nHello gcc!\ngreeting program\nLinux permissions\n' > notes.txt
cp notes.txt copy.txt
mv copy.txt moved.txt
ls -l
rm -- moved.txt
rmdir empty
set +x
step '三、查看内容：cat 全文，more/less 分页，head/tail 查看首尾；小文件可直接退出分页器'
set -x
cat notes.txt
more notes.txt < /dev/null
if command -v less; then
    LESS= LESSOPEN= less -F -X notes.txt < /dev/null
else
    printf '本机未安装 less：保留这一实际限制；安装后可执行 less notes.txt，按 q 退出。\n'
fi
head -n 2 notes.txt
tail -n 2 notes.txt
set +x
step '四、查找与权限：find 按文件名查找，whereis 定位 gcc，grep 搜索内容，chmod 修改权限'
set -x
find . -name '*.txt' -type f
whereis gcc
grep -n 'Linux' notes.txt
chmod 640 notes.txt
ls -l notes.txt
set +x
step '五、重定向和管道：覆盖、追加、标准错误重定向，以及过滤和行数统计'
set -x
printf 'first\n' > redirect.txt
printf 'second\n' >> redirect.txt
cat redirect.txt
ls missing-example 2> error.txt || printf '预期的查找失败，错误已写入 error.txt。\n'
cat error.txt
cat notes.txt | grep Linux | wc -l
set +x
step '六、备份压缩：tar 打包并恢复到新目录；gzip、bzip2 分别压缩副本，解压后比较内容'
set -x
tar -cvf notes.tar notes.txt
tar -tvf notes.tar
mkdir restored
tar -xvf notes.tar -C restored
cmp notes.txt restored/notes.txt
cp notes.txt gzip-copy.txt
gzip gzip-copy.txt
gzip -l gzip-copy.txt.gz
gzip -d gzip-copy.txt.gz
cmp notes.txt gzip-copy.txt
cp notes.txt bzip-copy.txt
bzip2 bzip-copy.txt
bzip2 -tv bzip-copy.txt.bz2
bzip2 -d bzip-copy.txt.bz2
cmp notes.txt bzip-copy.txt
cd ../../..
set +x
step '七、gcc 各阶段：-E 预处理，-S 编译为汇编，-c 汇编为目标文件，最后链接；-o 指定文件名'
set -x
mkdir "$record_dir/stages"
gcc -E hello.c -o "$record_dir/stages/hello.i"
gcc -S "$record_dir/stages/hello.i" -o "$record_dir/stages/hello.s"
gcc -c "$record_dir/stages/hello.s" -o "$record_dir/stages/hello.o"
gcc "$record_dir/stages/hello.o" -o "$record_dir/stages/hello"
head -n 10 "$record_dir/stages/hello.i"
head -n 20 "$record_dir/stages/hello.s"
file hello.c "$record_dir"/stages/hello.* "$record_dir/stages/hello"
"$record_dir/stages/hello"
test "$("$record_dir/stages/hello")" = 'Hello gcc!'
gcc -std=c11 -Wall -Wextra -Wpedantic -g hello.c -o "$record_dir/stages/hello_debug"
readelf -S "$record_dir/stages/hello_debug" | grep debug
set +x
step '八、多文件编译：分别生成目标文件后链接，通过 nm 观察函数的引用与定义'
set -x
gcc -std=c11 -Wall -Wextra -Wpedantic -g -c myapp.c -o "$record_dir/stages/myapp.o"
gcc -std=c11 -Wall -Wextra -Wpedantic -g -c greeting.c -o "$record_dir/stages/greeting.o"
nm "$record_dir/stages/myapp.o" "$record_dir/stages/greeting.o"
gcc "$record_dir/stages/myapp.o" "$record_dir/stages/greeting.o" -o "$record_dir/stages/myapp"
printf 'LinuxUser\n' | "$record_dir/stages/myapp"
set +x
step '九、Makefile：首次构建、重复构建、头文件依赖重编译，以及清理后重建；均在独立副本中进行'
set -x
mkdir "$record_dir/make"
cp hello.c myapp.c greeting.c greeting.h Makefile "$record_dir/make/"
make -C "$record_dir/make"
make -C "$record_dir/make"
sleep 1
touch "$record_dir/make/greeting.h"
make -C "$record_dir/make"
make -C "$record_dir/make" clean
make -C "$record_dir/make"
make
./hello
test "$(printf 'LinuxUser\n' | ./myapp)" = 'your name, please:Hello LinuxUser'
test "$(printf '123456789\n' | ./myapp)" = 'your name, please:Hello 123456789'
test "$(printf '123456789012345\n' | ./myapp)" = 'your name, please:Hello 123456789'
if ./myapp < /dev/null; then
    printf '验证失败：空输入应返回非零状态。\n'
    exit 1
else
    input_status=$?
    test "$input_status" -eq 1
    printf '空输入返回 1，符合预期。\n'
fi
printf 'LinuxUser\n' | ./myapp
set +x
step '全部验证通过：保留本次命令、标准输出、标准错误及中间产物'
printf '本次记录目录：%s\n' "$record_dir"

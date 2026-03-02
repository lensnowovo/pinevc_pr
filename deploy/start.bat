@echo off
REM PineVC-PR Windows 启动脚本
REM 用法: start.bat [命令]
REM
REM 命令:
REM   start     - 启动所有服务
REM   stop      - 停止所有服务
REM   restart   - 重启所有服务
REM   status    - 查看服务状态
REM   logs      - 查看日志
REM   down      - 停止并删除容器
REM   reset     - 完全重置 (包括数据)

setlocal enabledelayedexpansion

REM 切换到脚本目录
cd /d "%~dp0"

REM 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未安装或未运行
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo [提示] 未找到 .env 文件，正在创建...
    if exist .env.example (
        copy .env.example .env >nul
        echo [完成] .env 文件已创建，请编辑并填入必要的 API Key
    ) else (
        echo [警告] 请手动创建 .env 文件
    )
)

REM 获取命令参数
set CMD=%1
if "%CMD%"=="" set CMD=start

REM 执行命令
if "%CMD%"=="start" goto :start
if "%CMD%"=="stop" goto :stop
if "%CMD%"=="restart" goto :restart
if "%CMD%"=="status" goto :status
if "%CMD%"=="logs" goto :logs
if "%CMD%"=="down" goto :down
if "%CMD%"=="reset" goto :reset
goto :usage

:start
echo ============================================
echo   PineVC-PR 启动中...
echo ============================================
docker-compose up -d
echo.
echo ============================================
echo   服务启动成功!
echo ============================================
echo.
echo 访问地址:
echo   Dify Web:   http://localhost:3000
echo   Dify API:   http://localhost:5001
echo   n8n:        http://localhost:5678
echo   Weaviate:   http://localhost:8080
echo.
echo 首次使用请在 Dify 中设置管理员账号
echo.
goto :end

:stop
echo 停止所有服务...
docker-compose stop
echo 服务已停止
goto :end

:restart
echo 重启所有服务...
docker-compose restart
echo 服务已重启
goto :end

:status
echo 服务状态:
docker-compose ps
goto :end

:logs
if "%2"=="" (
    docker-compose logs -f --tail=100
) else (
    docker-compose logs -f --tail=100 %2
)
goto :end

:down
echo 停止并删除容器 (保留数据)...
docker-compose down
echo 容器已删除，数据卷保留
goto :end

:reset
echo [警告] 这将删除所有数据!
set /p confirm="确定要继续吗? (yes/no): "
if "%confirm%"=="yes" (
    docker-compose down -v
    echo 已完全重置
) else (
    echo 已取消
)
goto :end

:usage
echo 用法: %0 {start^|stop^|restart^|status^|logs^|down^|reset}
exit /b 1

:end
endlocal

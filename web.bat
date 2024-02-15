echo Installing npm dependencies...
call cd WebClient
call npm install

echo Running npm development server...
call  npm run dev --host


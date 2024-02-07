FROM node

USER node

WORKDIR /app

COPY --chown=node:node ./WebClient /app

RUN npm i

ENTRYPOINT npm run dev
FROM node:slim

WORKDIR /app/

COPY docker/hardhat/hardhat-project/ /app/

RUN npm install

RUN npm install --save-dev "hardhat@^3.1.7" "@types/node@^22.8.5" "typescript@~5.8.0"

EXPOSE 8545

CMD ["npx", "hardhat", "node"]
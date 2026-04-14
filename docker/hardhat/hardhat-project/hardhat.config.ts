import { defineConfig } from "hardhat/config";

export default defineConfig({
  solidity: {
    version: "0.8.28",
  },
  networks: {
    hardhat: {
      type: 'edr-simulated',
      accounts: {
        mnemonic: 'test test test test test test test test test test test junk',
        accountsBalance: 10n ** 23n
      },
      url: 'http://127.0.0.1:8545',
      blockGasLimit: 30000000,
    },
  },
});

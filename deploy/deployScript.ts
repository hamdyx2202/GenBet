import { readFileSync } from "fs";
import { TransactionStatus } from "genlayer-js/types";

export default async function main(client: any) {
  console.log("Deploying GenBet Prediction Market...");

  const contractCode = new Uint8Array(
    readFileSync("contracts/prediction_market.py")
  );

  const deployTx = await client.deployContract({
    code: contractCode,
    args: [
      "Will Bitcoin reach 100K by April 2026?",
      "Yes",
      "No",
      "https://www.coinmarketcap.com/currencies/bitcoin/"
    ],
  });

  console.log("Deploy TX:", deployTx);

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTx,
    status: TransactionStatus.ACCEPTED,
    retries: 200,
  });

  console.log(`GenBet deployed at: ${receipt.data.contract_address}`);

  return receipt.data.contract_address;
}

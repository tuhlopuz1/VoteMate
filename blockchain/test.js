import { ethers } from "ethers";
import dotenv from 'dotenv';
dotenv.config();

// Настройки
const clientWallet = ethers.Wallet.createRandom();
const clientAddress = clientWallet.address;
const contractAddress = process.env.CONTRACT_ADDRESS;
const BackendUrl = process.env.BACKEND_URL;
const BACKEND_PORT = process.env.BACKEND_PORT;
const provider = new ethers.JsonRpcProvider("http://localhost:8545");

// Функция для безопасной сериализации BigInt
function safeStringify(obj) {
    return JSON.stringify(obj, (key, value) => 
        typeof value === 'bigint' ? value.toString() : value
    );
}

async function getNonceFromForwarder(forwarderAddress, from) {
    const forwarderAbi = [
        "function getNonce(address from) view returns (uint256)"
    ];
    const forwarder = new ethers.Contract(forwarderAddress, forwarderAbi, provider);
    const nonce = await forwarder.getNonce(from);
    return nonce.toString(); // Преобразуем в строку
}

async function sendMetaTx(data) {
    const forwarderAddress = process.env.FORWARDER_CONTRACT_ADDRESS;
    const nonce = await getNonceFromForwarder(forwarderAddress, clientAddress);
    
    const request_to_sign = {
        from: clientAddress,
        to: contractAddress,
        value: 0,
        gas: 1_000_000,
        gasPrice: ethers.parseUnits('10', 'gwei').toString(), // Преобразуем в строку
        nonce: Number(nonce),
        data,
    };

    const domain = {
        name: "MinimalForwarder",
        version: "0.0.1",
        chainId: 1337,
        verifyingContract: forwarderAddress,
    };

    const types = {
        ForwardRequest: [
            { name: "from", type: "address" },
            { name: "to", type: "address" },
            { name: "value", type: "uint256" },
            { name: "gas", type: "uint256" },
            { name: "nonce", type: "uint256" },
            { name: "data", type: "bytes" },
        ],
    };

    const signature = await clientWallet.signTypedData(domain, types, request_to_sign);

    const request = {
        from_ad: clientAddress,
        to: contractAddress,
        value: 0,
        gas: 1_000_000,
        gasPrice: ethers.parseUnits('10', 'gwei').toString(), // Преобразуем в строку
        nonce: Number(nonce),
        data,
    };

    // Используем безопасную сериализацию
    const request_to_send = safeStringify({ request, signature });
    console.log("Request to send:", request_to_send);

    try {
        const relayRes = await fetch(`${BackendUrl}:${BACKEND_PORT}/relay`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: request_to_send,
        });

        if (!relayRes.ok) {
            throw new Error(`HTTP error! status: ${relayRes.status}`);
        }

        const relayResult = await relayRes.json();
        console.log("Relay tx result:", relayResult);

        return {
            txHash: relayResult.tx_hash,
            status: "success" // Упрощенный статус для примера
        };
    } catch (error) {
        console.error("Error in sendMetaTx:", error);
        throw error;
    }
}

async function Vote(topicId, option) {
    const ABI = [
        "function vote(string topicId, string option)"
    ];
    const iface = new ethers.Interface(ABI);
    const data = iface.encodeFunctionData("vote", [topicId, option]);
    
    try {
        const result = await sendMetaTx(data);
        console.log("Vote transaction completed:", result);
        return result;
    } catch (error) {
        console.error("Error in Vote:", error);
        throw error;
    }
}

Vote("3", "Option3")
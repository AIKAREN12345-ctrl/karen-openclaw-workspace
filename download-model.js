const { getLlama, resolveModelFile } = require('node-llama-cpp');

async function downloadModel() {
    console.log('Downloading embedding model...');
    const modelPath = await resolveModelFile(
        'hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf',
        { 
            llama: await getLlama(),
            dir: 'C:/Users/Karen/.cache/llama-models'
        }
    );
    console.log('Model downloaded to:', modelPath);
}

downloadModel().catch(console.error);

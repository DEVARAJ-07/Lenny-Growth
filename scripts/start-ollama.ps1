$env:Path = "$env:LOCALAPPDATA\Programs\Ollama;$env:Path"
$env:OLLAMA_MODELS = "D:\LLMs\ollama_store"
$env:OLLAMA_HOST = "127.0.0.1:11434"
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve

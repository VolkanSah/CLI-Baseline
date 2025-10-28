import React, { useState } from 'react';
import { Play, Download, Trash2, Settings } from 'lucide-react';

const models = [
  "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
  "deepseek/deepseek-chat-v3.1:free",
  "nvidia/nemotron-nano-9b-v2:free",
  "google/gemma-3-27b-it:free",
  "openai/gpt-oss-20b:free",
  "qwen/qwen3-coder:free",
  "qwen/qwen2.5-vl-72b-instruct:free",
  "nousresearch/deephermes-3-llama-3-8b-preview:free"
];

const categories = [
  "file_management", "text_processing", "system_info", 
  "network", "process_management", "permissions", 
  "archive", "search", "disk_usage"
];

export default function CLIDatasetGenerator() {
  const [apiKey, setApiKey] = useState('');
  const [selectedModels, setSelectedModels] = useState([models[0]]);
  const [commandsPerModel, setCommandsPerModel] = useState(5);
  const [dataset, setDataset] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState('');
  const [showSettings, setShowSettings] = useState(true);

  const systemPrompt = `Du bist ein Bash/Linux CLI Experte. Generiere EXAKTE, FUNKTIONIERENDE Bash-Commands mit detaillierten Erklärungen.

WICHTIG: Antworte NUR mit diesem JSON-Format, NICHTS ANDERES:
{
  "command": "der exakte bash command",
  "description": "kurze Beschreibung (deutsch)",
  "category": "eine der Kategorien",
  "example_output": "beispiel output",
  "use_case": "wann nutzt man das"
}

Kategorien: ${categories.join(', ')}`;

  const toggleModel = (model) => {
    setSelectedModels(prev => 
      prev.includes(model) 
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  };

  const callModel = async (model, category) => {
    const prompt = `Generiere einen praktischen Bash-Command für die Kategorie: ${category}. 
    
Beispiele für diese Kategorie:
- file_management: ls, cp, mv, rm, mkdir, touch, etc.
- text_processing: grep, sed, awk, cut, sort, etc.
- system_info: uname, df, free, top, ps, etc.

Antworte NUR mit dem JSON-Format, keine Erklärungen davor oder danach!`;

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': window.location.href,
      },
      body: JSON.stringify({
        model: model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: prompt }
        ],
        temperature: 0.8,
        max_tokens: 500
      })
    });

    if (!response.ok) {
      throw new Error(`Model ${model} failed: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices[0].message.content;
    
    // Extract JSON from response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Keine valide JSON-Antwort');
    }
    
    const parsed = JSON.parse(jsonMatch[0]);
    return {
      ...parsed,
      model: model.split('/')[1].split(':')[0],
      generated_at: new Date().toISOString()
    };
  };

  const generateDataset = async () => {
    if (!apiKey.trim()) {
      alert('Bitte OpenRouter API Key eingeben!');
      return;
    }

    if (selectedModels.length === 0) {
      alert('Bitte mindestens ein Modell auswählen!');
      return;
    }

    setIsRunning(true);
    setProgress('Starte Generation...');
    const newData = [];

    try {
      for (const model of selectedModels) {
        setProgress(`Arbeite mit ${model.split('/')[1]}...`);
        
        for (let i = 0; i < commandsPerModel; i++) {
          const category = categories[Math.floor(Math.random() * categories.length)];
          
          try {
            const entry = await callModel(model, category);
            newData.push(entry);
            setProgress(`${model.split('/')[1]}: ${i + 1}/${commandsPerModel} ✓`);
            
            // Update preview
            setDataset(prev => [...prev, entry]);
            
            // Rate limiting
            await new Promise(r => setTimeout(r, 1000));
          } catch (err) {
            setProgress(`${model.split('/')[1]}: Fehler bei ${i + 1} - ${err.message}`);
            await new Promise(r => setTimeout(r, 2000));
          }
        }
      }
      
      setProgress(`Fertig! ${newData.length} Commands generiert`);
    } catch (err) {
      setProgress(`Fehler: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const downloadDataset = () => {
    const jsonl = dataset.map(entry => JSON.stringify(entry)).join('\n');
    const blob = new Blob([jsonl], { type: 'application/jsonl' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bash_commands_${Date.now()}.jsonl`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadReadme = () => {
    const readme = `# Bash CLI Commands Dataset

## Dataset Info
- **Total Commands**: ${dataset.length}
- **Categories**: ${categories.join(', ')}
- **Generated**: ${new Date().toISOString()}
- **Models Used**: ${[...new Set(dataset.map(d => d.model))].join(', ')}

## Format
JSONL format with fields:
- \`command\`: The bash command
- \`description\`: German description
- \`category\`: Command category
- \`example_output\`: Example output
- \`use_case\`: When to use it
- \`model\`: Model that generated it
- \`generated_at\`: Timestamp

## Usage
\`\`\`python
from datasets import load_dataset
dataset = load_dataset("json", data_files="bash_commands.jsonl")
\`\`\`

## Upload to Hugging Face
\`\`\`bash
huggingface-cli login
huggingface-cli upload username/bash-commands . --repo-type dataset
\`\`\`
`;
    
    const blob = new Blob([readme], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'README.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-purple-300">CLI Dataset Generator</h1>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
            >
              <Settings className="text-purple-400" size={24} />
            </button>
          </div>
          
          {showSettings && (
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-purple-300 mb-2 font-semibold">OpenRouter API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-or-..."
                  className="w-full bg-slate-700/50 border border-purple-500/30 rounded-lg p-3 text-white"
                />
                <p className="text-purple-400/70 text-sm mt-1">
                  Get free key at: <a href="https://openrouter.ai" target="_blank" className="underline">openrouter.ai</a>
                </p>
              </div>

              <div>
                <label className="block text-purple-300 mb-2 font-semibold">
                  Commands pro Modell: {commandsPerModel}
                </label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={commandsPerModel}
                  onChange={(e) => setCommandsPerModel(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-purple-300 mb-2 font-semibold">Modelle auswählen</label>
                <div className="grid grid-cols-2 gap-2">
                  {models.map(model => (
                    <label key={model} className="flex items-center gap-2 bg-slate-700/30 p-2 rounded cursor-pointer hover:bg-slate-700/50">
                      <input
                        type="checkbox"
                        checked={selectedModels.includes(model)}
                        onChange={() => toggleModel(model)}
                        className="w-4 h-4"
                      />
                      <span className="text-purple-200 text-sm">{model.split('/')[1]}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={generateDataset}
              disabled={isRunning}
              className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-colors"
            >
              <Play size={20} />
              {isRunning ? 'Läuft...' : 'Dataset generieren'}
            </button>
            
            <button
              onClick={downloadDataset}
              disabled={dataset.length === 0}
              className="bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Download size={20} />
              JSONL
            </button>
            
            <button
              onClick={downloadReadme}
              disabled={dataset.length === 0}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Download size={20} />
              README
            </button>
            
            <button
              onClick={() => setDataset([])}
              disabled={dataset.length === 0}
              className="bg-red-600 hover:bg-red-700 disabled:bg-slate-600 text-white font-bold py-3 px-4 rounded-lg transition-colors"
            >
              <Trash2 size={20} />
            </button>
          </div>

          {progress && (
            <div className="mt-4 bg-slate-700/50 rounded-lg p-3 text-purple-300 font-mono text-sm">
              {progress}
            </div>
          )}
        </div>

        {dataset.length > 0 && (
          <div className="bg-slate-800/50 backdrop-blur border border-purple-500/30 rounded-xl p-6">
            <h2 className="text-xl font-bold text-purple-300 mb-4">
              Dataset Preview ({dataset.length} Einträge)
            </h2>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {dataset.slice(-10).reverse().map((entry, i) => (
                <div key={i} className="bg-slate-700/50 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-start justify-between mb-2">
                    <code className="text-green-400 font-mono text-sm bg-slate-900/50 px-2 py-1 rounded">
                      {entry.command}
                    </code>
                    <span className="text-purple-400 text-xs bg-purple-900/30 px-2 py-1 rounded">
                      {entry.category}
                    </span>
                  </div>
                  <p className="text-purple-200 text-sm mb-1">{entry.description}</p>
                  <p className="text-purple-400/70 text-xs">
                    Model: {entry.model} • {entry.use_case}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

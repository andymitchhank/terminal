async function runCommand(command: string) {
  const res = await fetch('/run', {
      method: 'POST', 
      headers: {'content-type': 'application/json;'},
      credentials: 'same-origin',
      body: JSON.stringify({ command: command })
    });
  return await res.json();
}

async function getPrompt() {
  const res = await fetch('/prompt', { credentials: 'same-origin' });
  return await res.text();
}

export { runCommand, getPrompt };
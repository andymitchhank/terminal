let runCommand = async (command: string) => {
  const res = await fetch('/run', {
      method: 'POST', 
      headers: {'content-type': 'application/json;'},
      credentials: 'same-origin',
      body: JSON.stringify({ command: command })
    });
  return await res.json();
}

let getPrompt = async () => {
  const res = await fetch('/prompt', { credentials: 'same-origin' });
  return await res.text();
}

export { runCommand, getPrompt };
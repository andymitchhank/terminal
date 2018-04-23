import * as React from 'react';
import * as CodeMirror from 'react-codemirror';

import { runCommand, TerminalResult } from '../api_services';

import 'codemirror/lib/codemirror.css';

interface State {
  newContent: string;
}

interface Props { 
  path: string;
  content: string;
  exit: () => void;
}

class EditorContext extends React.Component<Props, State> {

  constructor(props: Props) {
    super(props);
    this.state = {
      newContent: props.content
    };
  }

  saveContent = async () => {
    const result = await runCommand(`save "${this.props.path}" "${this.state.newContent}"`);
  }

  handleOnChange = (newText: string) => {
    this.setState({newContent: newText});
  }

  render() {
    return (
      <div id="editor">
        <div className="actions">
          <button onClick={this.props.exit}>Exit</button>
          <button onClick={this.saveContent}>Save</button>
        </div>
        <CodeMirror 
          value={this.props.content}
          onChange={this.handleOnChange}
          options={{lineNumbers: true, autofocus: true}}
        />
      </div>
    );
  }
}

export default EditorContext;
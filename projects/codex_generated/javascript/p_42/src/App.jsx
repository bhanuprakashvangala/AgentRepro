import React from 'react';
import { UIProvider, useUI } from './context/UIContext.jsx';
import { Button, Card, Modal } from './library.js';

function DemoContent() {
  const { openModal, closeModal, isModalOpen } = useUI();

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', background: '#f5f5f5', minHeight: '100vh' }}>
      <h1>Component Library Demo</h1>
      <Card title="Reusable Card">
        <p>Use our Button component to trigger modals or submit forms.</p>
        <Button variant="primary" onClick={openModal}>
          Launch Modal
        </Button>
      </Card>

      <Card title="Secondary Actions" variant="outline">
        <Button variant="secondary" onClick={() => alert('Secondary action')}>Secondary</Button>
        <Button variant="ghost" onClick={() => alert('Ghost action')} style={{ marginLeft: '1rem' }}>
          Ghost
        </Button>
      </Card>

      <Modal isOpen={isModalOpen} onClose={closeModal} title="Reusable Modal">
        <p>This modal is controlled through context state shared across the component tree.</p>
        <Button variant="primary" onClick={closeModal}>
          Close
        </Button>
      </Modal>
    </div>
  );
}

function App() {
  return (
    <UIProvider>
      <DemoContent />
    </UIProvider>
  );
}

export default App;

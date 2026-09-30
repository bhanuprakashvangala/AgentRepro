import React, { useEffect } from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: ${(props) => (props.isOpen ? 'flex' : 'none')};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const Content = styled.div`
  background: #ffffff;
  border-radius: 1rem;
  max-width: 500px;
  width: 90%;
  padding: 2rem;
  position: relative;
  box-shadow: 0 25px 50px -12px rgba(30, 64, 175, 0.3);
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  border: none;
  background: transparent;
  font-size: 1.25rem;
  cursor: pointer;
`;

const Title = styled.h3`
  margin-top: 0;
`;

function Modal({ isOpen, onClose, title, children }) {
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <Overlay isOpen={isOpen} onClick={onClose}>
      <Content onClick={(event) => event.stopPropagation()}>
        <CloseButton aria-label="Close modal" onClick={onClose}>
          ×
        </CloseButton>
        {title && <Title>{title}</Title>}
        {children}
      </Content>
    </Overlay>
  );
}

Modal.propTypes = {
  isOpen: PropTypes.bool,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string,
  children: PropTypes.node.isRequired
};

Modal.defaultProps = {
  isOpen: false,
  title: ''
};

export default Modal;

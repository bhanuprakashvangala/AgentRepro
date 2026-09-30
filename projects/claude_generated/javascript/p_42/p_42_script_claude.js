// ============================================================================
// src/context/ThemeContext.js - Theme management with Context API
// ============================================================================
import React, { createContext, useContext, useState } from 'react';
import PropTypes from 'prop-types';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  const themes = {
    light: {
      background: '#ffffff',
      text: '#000000',
      primary: '#007bff',
      secondary: '#6c757d',
      cardBackground: '#f8f9fa',
      border: '#dee2e6',
      modalOverlay: 'rgba(0, 0, 0, 0.5)',
    },
    dark: {
      background: '#1a1a1a',
      text: '#ffffff',
      primary: '#0d6efd',
      secondary: '#adb5bd',
      cardBackground: '#2d2d2d',
      border: '#495057',
      modalOverlay: 'rgba(0, 0, 0, 0.7)',
    },
  };

  const value = {
    theme,
    toggleTheme,
    colors: themes[theme],
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

ThemeProvider.propTypes = {
  children: PropTypes.node.isRequired,
};


// ============================================================================
// src/context/ModalContext.js - Modal state management
// ============================================================================
const ModalContext = createContext();

export const useModal = () => {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
};

export const ModalProvider = ({ children }) => {
  const [modals, setModals] = useState({});

  const openModal = (modalId) => {
    setModals((prev) => ({ ...prev, [modalId]: true }));
  };

  const closeModal = (modalId) => {
    setModals((prev) => ({ ...prev, [modalId]: false }));
  };

  const isModalOpen = (modalId) => {
    return modals[modalId] || false;
  };

  const value = {
    openModal,
    closeModal,
    isModalOpen,
  };

  return <ModalContext.Provider value={value}>{children}</ModalContext.Provider>;
};

ModalProvider.propTypes = {
  children: PropTypes.node.isRequired,
};


// ============================================================================
// src/components/Button/Button.js - Reusable button component
// ============================================================================
import styled from 'styled-components';

const StyledButton = styled.button`
  padding: ${(props) => {
    switch (props.$size) {
      case 'small':
        return '6px 12px';
      case 'large':
        return '12px 24px';
      default:
        return '8px 16px';
    }
  }};
  font-size: ${(props) => {
    switch (props.$size) {
      case 'small':
        return '12px';
      case 'large':
        return '18px';
      default:
        return '14px';
    }
  }};
  font-weight: 600;
  border-radius: 4px;
  border: none;
  cursor: ${(props) => (props.disabled ? 'not-allowed' : 'pointer')};
  transition: all 0.2s ease-in-out;
  opacity: ${(props) => (props.disabled ? 0.6 : 1)};

  background-color: ${(props) => {
    if (props.$variant === 'secondary') return props.$colors.secondary;
    if (props.$variant === 'outline') return 'transparent';
    return props.$colors.primary;
  }};

  color: ${(props) => {
    if (props.$variant === 'outline') return props.$colors.primary;
    return '#ffffff';
  }};

  border: ${(props) =>
    props.$variant === 'outline' ? `2px solid ${props.$colors.primary}` : 'none'};

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    opacity: 0.9;
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

export const Button = ({
  children,
  onClick,
  variant,
  size,
  disabled,
  type,
  className,
}) => {
  const { colors } = useTheme();

  return (
    <StyledButton
      onClick={onClick}
      $variant={variant}
      $size={size}
      disabled={disabled}
      type={type}
      className={className}
      $colors={colors}
    >
      {children}
    </StyledButton>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  disabled: PropTypes.bool,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  className: PropTypes.string,
};

Button.defaultProps = {
  onClick: () => {},
  variant: 'primary',
  size: 'medium',
  disabled: false,
  type: 'button',
  className: '',
};


// ============================================================================
// src/components/Card/Card.js - Reusable card component
// ============================================================================
const StyledCard = styled.div`
  background-color: ${(props) => props.$colors.cardBackground};
  border: 1px solid ${(props) => props.$colors.border};
  border-radius: 8px;
  padding: ${(props) => (props.$padding ? props.$padding : '20px')};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  width: ${(props) => (props.$width ? props.$width : 'auto')};
  height: ${(props) => (props.$height ? props.$height : 'auto')};

  ${(props) =>
    props.$hoverable &&
    `
    cursor: pointer;
    &:hover {
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
      transform: translateY(-4px);
    }
  `}
`;

const CardHeader = styled.div`
  font-size: 20px;
  font-weight: bold;
  color: ${(props) => props.$colors.text};
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid ${(props) => props.$colors.border};
`;

const CardBody = styled.div`
  color: ${(props) => props.$colors.text};
  font-size: 14px;
  line-height: 1.6;
`;

const CardFooter = styled.div`
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid ${(props) => props.$colors.border};
  color: ${(props) => props.$colors.text};
`;

export const Card = ({
  title,
  children,
  footer,
  hoverable,
  onClick,
  width,
  height,
  padding,
  className,
}) => {
  const { colors } = useTheme();

  return (
    <StyledCard
      $colors={colors}
      $hoverable={hoverable}
      onClick={onClick}
      $width={width}
      $height={height}
      $padding={padding}
      className={className}
    >
      {title && <CardHeader $colors={colors}>{title}</CardHeader>}
      <CardBody $colors={colors}>{children}</CardBody>
      {footer && <CardFooter $colors={colors}>{footer}</CardFooter>}
    </StyledCard>
  );
};

Card.propTypes = {
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  footer: PropTypes.node,
  hoverable: PropTypes.bool,
  onClick: PropTypes.func,
  width: PropTypes.string,
  height: PropTypes.string,
  padding: PropTypes.string,
  className: PropTypes.string,
};

Card.defaultProps = {
  title: null,
  footer: null,
  hoverable: false,
  onClick: null,
  width: 'auto',
  height: 'auto',
  padding: '20px',
  className: '',
};


// ============================================================================
// src/components/Modal/Modal.js - Reusable modal component
// ============================================================================
import { useEffect } from 'react';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${(props) => props.$colors.modalOverlay};
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-in-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
`;

const ModalContainer = styled.div`
  background-color: ${(props) => props.$colors.background};
  border-radius: 8px;
  padding: 0;
  max-width: ${(props) => props.$maxWidth || '500px'};
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-in-out;

  @keyframes slideIn {
    from {
      transform: translateY(-50px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`;

const ModalHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid ${(props) => props.$colors.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: ${(props) => props.$colors.text};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: ${(props) => props.$colors.text};
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${(props) => props.$colors.border};
  }
`;

const ModalBody = styled.div`
  padding: 20px;
  color: ${(props) => props.$colors.text};
`;

const ModalFooter = styled.div`
  padding: 20px;
  border-top: 1px solid ${(props) => props.$colors.border};
  display: flex;
  justify-content: flex-end;
  gap: 10px;
`;

export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  maxWidth,
  closeOnOverlayClick,
}) => {
  const { colors } = useTheme();

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <ModalOverlay $colors={colors} onClick={handleOverlayClick}>
      <ModalContainer $colors={colors} $maxWidth={maxWidth}>
        {title && (
          <ModalHeader $colors={colors}>
            <ModalTitle $colors={colors}>{title}</ModalTitle>
            <CloseButton $colors={colors} onClick={onClose}>
              &times;
            </CloseButton>
          </ModalHeader>
        )}
        <ModalBody $colors={colors}>{children}</ModalBody>
        {footer && <ModalFooter $colors={colors}>{footer}</ModalFooter>}
      </ModalContainer>
    </ModalOverlay>
  );
};

Modal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  footer: PropTypes.node,
  maxWidth: PropTypes.string,
  closeOnOverlayClick: PropTypes.bool,
};

Modal.defaultProps = {
  title: null,
  footer: null,
  maxWidth: '500px',
  closeOnOverlayClick: true,
};


// ============================================================================
// src/index.js - Library exports
// ============================================================================
export { Button } from './components/Button/Button';
export { Card } from './components/Card/Card';
export { Modal } from './components/Modal/Modal';
export { ThemeProvider, useTheme } from './context/ThemeContext';
export { ModalProvider, useModal } from './context/ModalContext';

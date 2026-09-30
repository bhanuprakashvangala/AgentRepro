import React from 'react';
import styled, { css } from 'styled-components';
import PropTypes from 'prop-types';

const variants = {
  primary: css`
    background: #2563eb;
    color: #fff;
    &:hover {
      background: #1d4ed8;
    }
  `,
  secondary: css`
    background: #10b981;
    color: #fff;
    &:hover {
      background: #059669;
    }
  `,
  outline: css`
    background: transparent;
    color: #2563eb;
    border: 2px solid #2563eb;
    &:hover {
      background: rgba(37, 99, 235, 0.1);
    }
  `,
  ghost: css`
    background: transparent;
    color: #111827;
    &:hover {
      background: rgba(17, 24, 39, 0.08);
    }
  `
};

const StyledButton = styled.button`
  font-size: 1rem;
  font-weight: 600;
  border-radius: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  ${(props) => variants[props.variant] || variants.primary};

  &:active {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

function Button({ children, variant, ...rest }) {
  return (
    <StyledButton variant={variant} {...rest}>
      {children}
    </StyledButton>
  );
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'ghost'])
};

Button.defaultProps = {
  variant: 'primary'
};

export default Button;

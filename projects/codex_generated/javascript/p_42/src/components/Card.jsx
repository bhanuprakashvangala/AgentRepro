import React from 'react';
import styled, { css } from 'styled-components';
import PropTypes from 'prop-types';

const variantStyles = {
  filled: css`
    background: #ffffff;
    box-shadow: 0 15px 30px rgba(15, 23, 42, 0.08);
  `,
  outline: css`
    background: transparent;
    border: 2px solid rgba(148, 163, 184, 0.4);
  `
};

const CardWrapper = styled.section`
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  ${(props) => variantStyles[props.variant] || variantStyles.filled};

  &:hover {
    transform: translateY(-2px);
  }
`;

const Title = styled.h2`
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.25rem;
`;

function Card({ title, children, variant }) {
  return (
    <CardWrapper variant={variant}>
      {title && <Title>{title}</Title>}
      {children}
    </CardWrapper>
  );
}

Card.propTypes = {
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['filled', 'outline'])
};

Card.defaultProps = {
  title: '',
  variant: 'filled'
};

export default Card;

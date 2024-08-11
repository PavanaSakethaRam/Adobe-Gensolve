import React from 'react';
import './loading.scss';

export function LoadingScreen() {
  return (
    <div className="loading">
      {[...Array(4)].map((_, rowIndex) => (
        <div className="row" key={rowIndex}>
          {[...Array(4)].map((_, pointIndex) => (
            <div className="point" key={pointIndex}></div>
          ))}
        </div>
      ))}
    </div>
  );
};
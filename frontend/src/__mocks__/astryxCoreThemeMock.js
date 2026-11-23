import React from 'react';

export const Theme = ({ children }) => <>{children}</>;
export const useTheme = () => ({ theme: 'neutral' });

const themeExports = {
    Theme,
    useTheme,
};

export default themeExports;

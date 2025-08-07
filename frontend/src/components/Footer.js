import React from 'react';
import { useTheme } from '../context/ThemeContext';

const Footer = () => {
  const { theme } = useTheme();

  // Don't render footer if disabled
  if (theme.footer_enabled === 'false') {
    return null;
  }

  let footerLinks = {};
  try {
    footerLinks = JSON.parse(theme.footer_links || '{}');
  } catch (e) {
    console.error('Error parsing footer links:', e);
  }

  return (
    <footer className="footer">
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        {/* Footer Links */}
        {Object.keys(footerLinks).length > 0 && (
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            {Object.entries(footerLinks).map(([label, url]) => (
              <a
                key={label}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: 'inherit',
                  textDecoration: 'none',
                  fontSize: '14px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.textDecoration = 'underline';
                }}
                onMouseLeave={(e) => {
                  e.target.style.textDecoration = 'none';
                }}
              >
                {label}
              </a>
            ))}
          </div>
        )}

        {/* Footer Text */}
        <div style={{ 
          flex: Object.keys(footerLinks).length > 0 ? 'none' : '1',
          textAlign: Object.keys(footerLinks).length > 0 ? 'right' : 'center',
          fontSize: '14px'
        }}>
          {theme.footer_text || 'Powered by LXCloud'}
        </div>
      </div>
    </footer>
  );
};

export default Footer;
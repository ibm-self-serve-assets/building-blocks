import React from 'react';
import {
  Header as CarbonHeader,
  HeaderName,
  HeaderGlobalBar,
  HeaderGlobalAction,
} from '@carbon/react';
import { Information, Renew } from '@carbon/icons-react';

const Header = () => {
  return (
    <CarbonHeader aria-label="Maximo Modernization">
      <HeaderName prefix="">
        Maximo Modernization
      </HeaderName>
      <HeaderGlobalBar>
        <HeaderGlobalAction
          aria-label="Refresh"
          tooltipAlignment="end"
          onClick={() => window.location.reload()}
        >
          <Renew size={20} />
        </HeaderGlobalAction>
        <HeaderGlobalAction
          aria-label="About"
          tooltipAlignment="end"
        >
          <Information size={20} />
        </HeaderGlobalAction>
      </HeaderGlobalBar>
    </CarbonHeader>
  );
};

export default Header;

// Made with Bob

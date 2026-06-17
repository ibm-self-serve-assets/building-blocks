import React, { useState, useEffect } from 'react';
import {
  Grid,
  Column,
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  TableToolbar,
  TableToolbarContent,
  TableToolbarSearch,
  Button,
  Tag,
  Loading,
  InlineNotification,
  Dropdown,
} from '@carbon/react';
import { Renew, View } from '@carbon/icons-react';
import { scriptAPI } from '../services/api';

const ScriptList = ({ onSelectScript }) => {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterLanguage, setFilterLanguage] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    // Check if Maximo configuration exists before fetching
    const savedConfig = localStorage.getItem('maximoConfig');
    if (savedConfig) {
      fetchScripts();
    } else {
      setLoading(false);
      setError('Please configure your Maximo connection in the Configuration tab first.');
    }
  }, []);

  const fetchScripts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scriptAPI.getAllScripts();
      setScripts(data.scripts || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get field value (handles spi: namespace)
  const getField = (script, fieldName) => {
    return script[`spi:${fieldName}`] || script[fieldName] || '';
  };

  const getUniqueLanguages = () => {
    const languages = new Set(scripts.map(s => getField(s, 'scriptlanguage')).filter(Boolean));
    return [{ id: 'all', label: 'All Languages' }, ...Array.from(languages).map(lang => ({ id: lang, label: lang }))];
  };

  const getUniqueStatuses = () => {
    const statuses = new Set(scripts.map(s => getField(s, 'status')).filter(Boolean));
    return [{ id: 'all', label: 'All Statuses' }, ...Array.from(statuses).map(status => ({ id: status, label: status }))];
  };

  const filteredScripts = scripts.filter(script => {
    const scriptLang = getField(script, 'scriptlanguage');
    const scriptStatus = getField(script, 'status');
    const langMatch = filterLanguage === 'all' || scriptLang === filterLanguage;
    const statusMatch = filterStatus === 'all' || scriptStatus === filterStatus;
    return langMatch && statusMatch;
  });

  const headers = [
    { key: 'autoscript', header: 'Script Name' },
    { key: 'scriptlanguage', header: 'Language' },
    { key: 'status', header: 'Status' },
    { key: 'description', header: 'Description' },
    { key: 'active', header: 'Active' },
    { key: 'actions', header: 'Actions' },
  ];

  const rows = filteredScripts.map((script) => {
    const scriptName = getField(script, 'autoscript');
    const isActive = getField(script, 'active');
    
    return {
      id: scriptName || `script-${Math.random()}`,
      autoscript: scriptName,
      scriptlanguage: getField(script, 'scriptlanguage'),
      status: getField(script, 'status'),
      description: getField(script, 'description') || '-',
      active: isActive === true || isActive === 'true' || isActive === 1 ? 'Yes' : 'No',
      actions: script,
    };
  });

  if (loading) {
    return (
      <Grid>
        <Column sm={4} md={8} lg={16}>
          <Loading description="Loading scripts..." withOverlay={false} />
        </Column>
      </Grid>
    );
  }

  if (error) {
    return (
      <Grid>
        <Column sm={4} md={8} lg={16}>
          <InlineNotification
            kind="error"
            title="Error loading scripts"
            subtitle={error}
            lowContrast
          />
        </Column>
      </Grid>
    );
  }

  return (
    <Grid>
      <Column sm={4} md={8} lg={16}>
        <DataTable rows={rows} headers={headers}>
          {({
            rows,
            headers,
            getHeaderProps,
            getRowProps,
            getTableProps,
            getTableContainerProps,
            onInputChange,
          }) => (
            <TableContainer
              title="Automation Scripts"
              description={`${filteredScripts.length} scripts found`}
              {...getTableContainerProps()}
            >
              <TableToolbar>
                <TableToolbarContent>
                  <TableToolbarSearch
                    persistent
                    placeholder="Search scripts..."
                    onChange={onInputChange}
                  />
                  <Dropdown
                    id="language-filter"
                    titleText=""
                    label="Filter by language"
                    items={getUniqueLanguages()}
                    itemToString={(item) => (item ? item.label : '')}
                    selectedItem={getUniqueLanguages().find(l => l.id === filterLanguage)}
                    onChange={({ selectedItem }) => setFilterLanguage(selectedItem.id)}
                  />
                  <Dropdown
                    id="status-filter"
                    titleText=""
                    label="Filter by status"
                    items={getUniqueStatuses()}
                    itemToString={(item) => (item ? item.label : '')}
                    selectedItem={getUniqueStatuses().find(s => s.id === filterStatus)}
                    onChange={({ selectedItem }) => setFilterStatus(selectedItem.id)}
                  />
                  <Button
                    kind="ghost"
                    renderIcon={Renew}
                    onClick={fetchScripts}
                  >
                    Refresh
                  </Button>
                </TableToolbarContent>
              </TableToolbar>
              <Table {...getTableProps()}>
                <TableHead>
                  <TableRow>
                    {headers.map((header) => (
                      <TableHeader {...getHeaderProps({ header })} key={header.key}>
                        {header.header}
                      </TableHeader>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rows.map((row) => (
                    <TableRow {...getRowProps({ row })} key={row.id}>
                      {row.cells.map((cell) => {
                        if (cell.info.header === 'scriptlanguage') {
                          return (
                            <TableCell key={cell.id}>
                              <Tag type="blue">{cell.value}</Tag>
                            </TableCell>
                          );
                        }
                        if (cell.info.header === 'status') {
                          return (
                            <TableCell key={cell.id}>
                              <Tag type={cell.value === 'ACTIVE' ? 'green' : 'warm-gray'}>
                                {cell.value}
                              </Tag>
                            </TableCell>
                          );
                        }
                        if (cell.info.header === 'actions') {
                          return (
                            <TableCell key={cell.id}>
                              <Button
                                kind="ghost"
                                size="sm"
                                renderIcon={View}
                                onClick={() => onSelectScript(cell.value)}
                              >
                                View
                              </Button>
                            </TableCell>
                          );
                        }
                        return <TableCell key={cell.id}>{cell.value}</TableCell>;
                      })}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DataTable>
      </Column>
    </Grid>
  );
};

export default ScriptList;

// Made with Bob

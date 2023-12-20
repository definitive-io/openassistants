import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { cn } from '../lib/utils';

import React from 'react';

export const DataframeTable = ({
  dataframe,
  title,
}: {
  dataframe: any;
  title: string;
}) => {
  return (
    <div
      className="max-h-96 overflow-y-auto px-4 mx-auto overflow-x-auto"
      style={{ maxWidth: '90vw' }}
    >
      <h2 className={cn('text-xl text-center text-primary mb-4')}>{title}</h2>
      <Table
        className={cn(
          'w-full table-auto divide-y divide-gray-700 sm:table-fixed'
        )}
      >
        <TableHeader>
          <TableRow>
            {dataframe.columns.map((column: any, index: any) => (
              <TableHead
                key={`table_head_${index}`}
                className={cn(
                  'px-2 py-1 text-left text-sm font-medium uppercase sm:w-auto whitespace-normal'
                )}
              >
                {column && String(column).replace(/_/g, ' ')}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody className={cn('divide-y')}>
          {dataframe.data.map((row: any, rowIndex: any) => (
            <TableRow key={`table_row_${rowIndex}`}>
              {row.map((cell: any, cellIndex: any) => (
                <TableCell
                  key={`table_cell_${rowIndex}_${cellIndex}`}
                  className={cn(
                    'whitespace-normal px-2 py-1 text-sm sm:w-auto overflow-hidden truncate text-primary'
                  )}
                >
                  {cell}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

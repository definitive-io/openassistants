import React from 'react';
import Plot from 'react-plotly.js';
interface RenderVisMessageProps {
  id: string;
  data: any;
  layout: any;
}

export const RenderVisMessage = ({
  id,
  data,
  layout,
}: RenderVisMessageProps) => {
  if (data && layout) {
    return (
      <div className="overflow-x-auto">
        {/* <div>TODO VIS</div> */}
        <Plot data={data} layout={layout}></Plot>
      </div>
    );
  }
  return <div></div>;
};

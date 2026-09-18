function TableVisualization({ visualization }) {
  const data = Array.isArray(visualization.data)
    ? visualization.data
    : [];

  if (data.length === 0) {
    return <p>No data available for this visualization.</p>;
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => (
                <td key={column}>
                  {row[column] === null ||
                  row[column] === undefined
                    ? "—"
                    : String(row[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TableVisualization;
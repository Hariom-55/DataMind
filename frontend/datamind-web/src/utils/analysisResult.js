function isObject(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  );
}

function normalizeAnalysisResult(response) {
  if (!isObject(response)) {
    return null;
  }

  let current = response;

  for (let depth = 0; depth < 5; depth += 1) {
    if (
      current.analysis ||
      current.insights ||
      current.visualizations
    ) {
      return current;
    }

    if (
      isObject(current.result)
    ) {
      current = current.result;
      continue;
    }

    break;
  }

  return current;
}

export {
  normalizeAnalysisResult,
};
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

  return isObject(response.result) ? response.result : response;
}

export {
  normalizeAnalysisResult,
};

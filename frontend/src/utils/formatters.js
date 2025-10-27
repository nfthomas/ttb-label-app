export const formatFileSize = (sizeInBytes) => {
  if (!sizeInBytes) return '0 KB';
  const kb = sizeInBytes / 1024;
  return kb < 1024 ? `${Math.round(kb)} KB` : `${(kb / 1024).toFixed(1)} MB`;
};

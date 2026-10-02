(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.04b5ffdc3b9a2625.js","sha256":"04b5ffdc3b9a2625c7664d72c8a0079d49e3b50974686cd78d9ca88c03a869cd","count":247});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());

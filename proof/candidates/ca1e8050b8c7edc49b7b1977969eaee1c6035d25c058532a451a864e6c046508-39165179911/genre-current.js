(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.cde2554b3c3c6db8.js","sha256":"cde2554b3c3c6db891b8e325b7400a1c95be529f3c1cd0dfc33b110203a27e81","count":244});
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

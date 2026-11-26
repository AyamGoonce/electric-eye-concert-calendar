(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b3cbcef9c636d05b.js","sha256":"b3cbcef9c636d05b0d4cfda56e52b2f250122c9dd6b8d6a3e23074c7a6a2510e","count":244});
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

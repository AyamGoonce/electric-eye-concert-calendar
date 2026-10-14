(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0aa0ead8994d30fc.js","sha256":"0aa0ead8994d30fc562c81fed2cdeab1fb63a29c9771f97dbebc950dfadf7ff2","count":244});
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

(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d7316925155f1f3a.js","sha256":"d7316925155f1f3a22e7fbf0329e67e46168cdc192be0a869f051cec82082419","count":245});
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

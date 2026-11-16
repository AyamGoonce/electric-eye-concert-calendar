(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b8958c97fb968e66.js","sha256":"b8958c97fb968e66c42cbf7f2f32d5ac4d79f18a3ec431805887c88270395772","count":244});
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

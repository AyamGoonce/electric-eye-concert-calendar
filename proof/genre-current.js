(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b97af8f29b59e28f.js","sha256":"b97af8f29b59e28f942d4ea13c9595af4f703d00302852e7df9fc041fb6ede0f","count":244});
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

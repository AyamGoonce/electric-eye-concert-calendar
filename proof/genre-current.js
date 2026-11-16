(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.2d47ff97c6ad98fc.js","sha256":"2d47ff97c6ad98fca29912abe7db366e35aef21ada821e53e47b1ea31cd88a90","count":244});
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

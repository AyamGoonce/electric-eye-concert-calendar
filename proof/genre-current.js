(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7c82ac5913d24576.js","sha256":"7c82ac5913d245764cd9f931adf3ca860188143e5aa15a6b09647d90c3b956c2","count":244});
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

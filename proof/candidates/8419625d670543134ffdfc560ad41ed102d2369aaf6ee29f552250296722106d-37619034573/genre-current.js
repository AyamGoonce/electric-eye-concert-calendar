(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ce303dd7f8252d3f.js","sha256":"ce303dd7f8252d3f19187b1e1248db7b8d83c2d015c16016ca762c6d180c26db","count":244});
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

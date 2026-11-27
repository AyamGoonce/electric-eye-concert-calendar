(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ea9c5a44635e1ac8.js","sha256":"ea9c5a44635e1ac8008d8ec142fe3e94ea5dd2f4db2636b94c3a6f8b3d4a838c","count":244});
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

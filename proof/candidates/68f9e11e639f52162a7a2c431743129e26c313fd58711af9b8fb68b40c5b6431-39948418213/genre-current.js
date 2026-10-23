(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.806b889fe39b05fc.js","sha256":"806b889fe39b05fc2ab55a2ee4d97c95f37f2786a15e3daaafb158573c1c9f00","count":244});
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

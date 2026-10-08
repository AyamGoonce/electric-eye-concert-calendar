(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f0235e454ba08ff4.js","sha256":"f0235e454ba08ff493bb7bbe3d48a3f125b2b8fbee20e8ed21506ecc14c19c6e","count":244});
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

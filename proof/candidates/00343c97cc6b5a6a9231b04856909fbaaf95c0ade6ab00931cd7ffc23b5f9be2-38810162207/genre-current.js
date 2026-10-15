(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.1188af6ff00c9afc.js","sha256":"1188af6ff00c9afc8bfc4db88f6c20ac78f7f6b25f32e31e26b14383fbb825e8","count":244});
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

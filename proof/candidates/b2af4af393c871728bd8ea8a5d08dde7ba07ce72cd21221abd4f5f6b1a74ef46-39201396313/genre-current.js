(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.4470f34641bd8d53.js","sha256":"4470f34641bd8d536ee8ae41ffa6465bf5169bf79a8c3a2409a0654b2d6eae06","count":244});
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

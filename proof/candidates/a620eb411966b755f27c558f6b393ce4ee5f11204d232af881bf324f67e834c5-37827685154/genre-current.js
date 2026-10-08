(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.264086a8109e8926.js","sha256":"264086a8109e8926d2fd1dec0bc8edc5e64fc2625b39f4797a911bfe93d21655","count":244});
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

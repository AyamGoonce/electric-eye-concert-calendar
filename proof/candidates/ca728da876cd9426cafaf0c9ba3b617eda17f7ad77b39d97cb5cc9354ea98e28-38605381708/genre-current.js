(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7151a36fc0eda852.js","sha256":"7151a36fc0eda85272cd89a7b99129c039ddfd8d9e12c5ddf5cfae3d3ddc190d","count":244});
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

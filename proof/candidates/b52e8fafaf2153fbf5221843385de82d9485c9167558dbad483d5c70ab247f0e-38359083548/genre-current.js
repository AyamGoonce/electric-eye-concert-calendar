(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.4fb6edba7cde5687.js","sha256":"4fb6edba7cde56873c44ba0018a1d03d9e29434a47db9822eb64ae9dc8433412","count":244});
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

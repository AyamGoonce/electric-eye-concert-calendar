(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.4b1bb0f2506d4fb1.js","sha256":"4b1bb0f2506d4fb18b96ad271f7716e5149a0c21443126dc0b6a05c45a178a28","count":244});
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

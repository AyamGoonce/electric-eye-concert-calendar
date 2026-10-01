(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ddee282c49b4d4e5.js","sha256":"ddee282c49b4d4e53acffc1e5768dc5932e7cd3e16ecad8a957337e66a950c44","count":208});
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

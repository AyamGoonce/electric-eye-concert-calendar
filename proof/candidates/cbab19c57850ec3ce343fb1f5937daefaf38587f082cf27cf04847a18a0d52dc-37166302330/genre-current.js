(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.2fec1acbde766c93.js","sha256":"2fec1acbde766c939ee39f1d3fc9af728576c332708e1374d6782dbdeea4e89a","count":244});
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

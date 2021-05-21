# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SentimentAnalysisApp.py'],
             pathex=['C:\\Users\\John\\PycharmProjects\\TwitterSentimentAnalysisV1'],
             binaries=[],
             datas=[],
             hiddenimports=["sklearn.utils._weight_vector", "matplotlib.*"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
	  Tree('.\\pickled-algorithms', prefix='pickled-algorithms\\'),
          a.zipfiles,
          a.datas,
          [],
          name='Main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )

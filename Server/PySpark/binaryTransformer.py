from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param, Params, TypeConverters
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql import DataFrame
from pyspark.sql.types import StringType, IntegerType
import pyspark.sql.functions as F

class BinaryTransformer(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable):
    input_col = Param(Params._dummy(), "input_col", "input column name.", typeConverter=TypeConverters.toString)
    output_col = Param(Params._dummy(), "output_col", "output column name.", typeConverter=TypeConverters.toString)
  
    @keyword_only
    def __init__(self, input_col: str = "input", output_col: str = "output"):
        super(BinaryTransformer, self).__init__()
        self._setDefault(input_col=None, output_col=None)
        kwargs = self._input_kwargs
        self.set_params(**kwargs)
    
    @keyword_only
    def set_params(self, input_col: str = "input", output_col: str = "output"):
        kwargs = self._input_kwargs
        self._set(**kwargs)
    
    def get_input_col(self):
        return self.getOrDefault(self.input_col)
  
    def get_output_col(self):
        return self.getOrDefault(self.output_col)
  
    def _transform(self, df: DataFrame):
        encodeHeartDisease = {'Yes':'1', 'No':'0'}
        df = df.replace(encodeHeartDisease, subset=['HeartDisease'])
        return df.withColumn("HeartDisease", F.col("HeartDisease").astype(IntegerType()))